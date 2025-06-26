# src/intelligence/generators/landing_page/utils/validation.py
"""
Input validation utilities for landing page generation.
Validates and sanitizes all inputs to ensure system reliability and security.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
from urllib.parse import urlparse
import bleach

from ..core.types import PageType, ColorScheme, GenerationPreferences
from ..analytics.events import EventType, ConversionType, DeviceType

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class ValidationResult:
    """Result of validation with details"""
    
    def __init__(self, is_valid: bool, data: Any = None, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.data = data
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, error: str):
        """Add validation error"""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add validation warning"""
        self.warnings.append(warning)

def validate_preferences(preferences: Dict[str, Any]) -> GenerationPreferences:
    """
    Validate and sanitize user preferences for landing page generation
    
    Args:
        preferences: Raw preferences dict from user input
        
    Returns:
        GenerationPreferences: Validated and sanitized preferences
        
    Raises:
        ValidationError: If validation fails
    """
    
    try:
        # Set defaults
        validated = {
            'page_type': PageType.LEAD_GENERATION,
            'color_scheme': ColorScheme.PROFESSIONAL,
            'target_audience': {},
            'brand_guidelines': {},
            'conversion_goals': [],
            'content_style': 'professional',
            'generate_variants': False,
            'mobile_first': True,
            'seo_optimization': True,
            'analytics_tracking': True,
            'expected_traffic': 100,
            'average_order_value': 0,
            'customer_lifetime_value': 0
        }
        
        # Validate page type
        if 'page_type' in preferences:
            page_type_str = str(preferences['page_type']).upper()
            try:
                validated['page_type'] = PageType[page_type_str]
            except KeyError:
                logger.warning(f"Invalid page type: {preferences['page_type']}, using default")
        
        # Validate color scheme
        if 'color_scheme' in preferences:
            color_scheme_str = str(preferences['color_scheme']).upper()
            try:
                validated['color_scheme'] = ColorScheme[color_scheme_str]
            except KeyError:
                logger.warning(f"Invalid color scheme: {preferences['color_scheme']}, using default")
        
        # Validate target audience
        if 'target_audience' in preferences:
            validated['target_audience'] = validate_target_audience(preferences['target_audience'])
        
        # Validate brand guidelines
        if 'brand_guidelines' in preferences:
            validated['brand_guidelines'] = validate_brand_guidelines(preferences['brand_guidelines'])
        
        # Validate conversion goals
        if 'conversion_goals' in preferences:
            validated['conversion_goals'] = validate_conversion_goals(preferences['conversion_goals'])
        
        # Validate content style
        if 'content_style' in preferences:
            style = sanitize_string(preferences['content_style'])
            if style in ['professional', 'casual', 'friendly', 'authoritative', 'conversational']:
                validated['content_style'] = style
        
        # Validate boolean flags
        boolean_fields = ['generate_variants', 'mobile_first', 'seo_optimization', 'analytics_tracking']
        for field in boolean_fields:
            if field in preferences:
                validated[field] = bool(preferences[field])
        
        # Validate numeric fields
        if 'expected_traffic' in preferences:
            traffic = validate_positive_integer(preferences['expected_traffic'], 'expected_traffic')
            validated['expected_traffic'] = min(100000, max(1, traffic))  # Cap between 1-100k
        
        if 'average_order_value' in preferences:
            aov = validate_positive_number(preferences['average_order_value'], 'average_order_value')
            validated['average_order_value'] = max(0, aov)
        
        if 'customer_lifetime_value' in preferences:
            clv = validate_positive_number(preferences['customer_lifetime_value'], 'customer_lifetime_value')
            validated['customer_lifetime_value'] = max(0, clv)
        
        return GenerationPreferences(**validated)
        
    except Exception as e:
        logger.error(f"Preferences validation failed: {str(e)}")
        raise ValidationError(f"Invalid preferences: {str(e)}")

def validate_intelligence_data(intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize intelligence data
    
    Args:
        intelligence_data: Raw intelligence data
        
    Returns:
        Dict[str, Any]: Validated intelligence data
        
    Raises:
        ValidationError: If validation fails
    """
    
    result = ValidationResult(True, {})
    
    try:
        # Required fields
        if not intelligence_data:
            result.add_error("Intelligence data cannot be empty")
            
        # Validate confidence score
        if 'confidence_score' in intelligence_data:
            confidence = validate_confidence_score(intelligence_data['confidence_score'])
            result.data['confidence_score'] = confidence
        else:
            result.data['confidence_score'] = 0.5  # Default medium confidence
        
        # Validate competitors data
        if 'competitors' in intelligence_data:
            competitors = validate_competitors_data(intelligence_data['competitors'])
            result.data['competitors'] = competitors
        else:
            result.data['competitors'] = []
            result.add_warning("No competitor data provided")
        
        # Validate product information
        if 'product_info' in intelligence_data:
            product_info = validate_product_info(intelligence_data['product_info'])
            result.data['product_info'] = product_info
        else:
            result.add_error("Product information is required")
        
        # Validate market intelligence
        if 'market_intelligence' in intelligence_data:
            market_intel = validate_market_intelligence(intelligence_data['market_intelligence'])
            result.data['market_intelligence'] = market_intel
        else:
            result.data['market_intelligence'] = {}
        
        # Validate conversion intelligence
        if 'conversion_intelligence' in intelligence_data:
            conv_intel = validate_conversion_intelligence(intelligence_data['conversion_intelligence'])
            result.data['conversion_intelligence'] = conv_intel
        else:
            result.data['conversion_intelligence'] = {}
        
        # Validate detected niche
        if 'detected_niche' in intelligence_data:
            niche = sanitize_string(intelligence_data['detected_niche'])
            if niche in ['health', 'business', 'technology', 'finance', 'education', 'lifestyle']:
                result.data['detected_niche'] = niche
            else:
                result.data['detected_niche'] = 'business'  # Default
                result.add_warning(f"Unknown niche '{niche}', using 'business'")
        
        if not result.is_valid:
            raise ValidationError(f"Intelligence validation failed: {', '.join(result.errors)}")
        
        if result.warnings:
            logger.warning(f"Intelligence validation warnings: {', '.join(result.warnings)}")
        
        return result.data
        
    except Exception as e:
        logger.error(f"Intelligence data validation failed: {str(e)}")
        raise ValidationError(f"Invalid intelligence data: {str(e)}")

def validate_target_audience(audience_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate target audience data"""
    
    validated = {}
    
    # Demographics
    if 'age_range' in audience_data:
        age_range = audience_data['age_range']
        if isinstance(age_range, dict) and 'min' in age_range and 'max' in age_range:
            min_age = validate_positive_integer(age_range['min'], 'min_age')
            max_age = validate_positive_integer(age_range['max'], 'max_age')
            validated['age_range'] = {'min': max(13, min_age), 'max': min(120, max_age)}
    
    # Income level
    if 'income_level' in audience_data:
        income = sanitize_string(audience_data['income_level'])
        if income in ['low', 'middle', 'high', 'mixed']:
            validated['income_level'] = income
    
    # Interests
    if 'interests' in audience_data:
        if isinstance(audience_data['interests'], list):
            validated['interests'] = [
                sanitize_string(interest) 
                for interest in audience_data['interests'][:10]  # Max 10 interests
            ]
    
    # Pain points
    if 'pain_points' in audience_data:
        if isinstance(audience_data['pain_points'], list):
            validated['pain_points'] = [
                sanitize_string(pain_point) 
                for pain_point in audience_data['pain_points'][:10]  # Max 10 pain points
            ]
    
    return validated

def validate_brand_guidelines(brand_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate brand guidelines data"""
    
    validated = {}
    
    # Brand colors
    if 'colors' in brand_data:
        colors = validate_brand_colors(brand_data['colors'])
        validated['colors'] = colors
    
    # Typography
    if 'typography' in brand_data:
        typography = validate_typography(brand_data['typography'])
        validated['typography'] = typography
    
    # Voice and tone
    if 'voice_tone' in brand_data:
        voice_tone = sanitize_string(brand_data['voice_tone'])
        if voice_tone in ['professional', 'friendly', 'authoritative', 'casual', 'playful']:
            validated['voice_tone'] = voice_tone
    
    # Logo URL
    if 'logo_url' in brand_data:
        logo_url = validate_url(brand_data['logo_url'])
        if logo_url:
            validated['logo_url'] = logo_url
    
    return validated

def validate_brand_colors(colors_data: Dict[str, Any]) -> Dict[str, str]:
    """Validate brand color data"""
    
    validated = {}
    
    color_fields = ['primary', 'secondary', 'accent', 'background', 'text']
    
    for field in color_fields:
        if field in colors_data:
            color = validate_color(colors_data[field])
            if color:
                validated[field] = color
    
    return validated

def validate_color(color_value: str) -> Optional[str]:
    """Validate color value (hex, rgb, or named color)"""
    
    if not isinstance(color_value, str):
        return None
    
    color = color_value.strip()
    
    # Hex color validation
    hex_pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    if re.match(hex_pattern, color):
        return color
    
    # RGB color validation
    rgb_pattern = r'^rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)$'
    rgb_match = re.match(rgb_pattern, color, re.IGNORECASE)
    if rgb_match:
        r, g, b = map(int, rgb_match.groups())
        if all(0 <= val <= 255 for val in [r, g, b]):
            return color.lower()
    
    # Named colors (basic set)
    named_colors = {
        'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown',
        'black', 'white', 'gray', 'grey', 'navy', 'teal', 'maroon', 'olive'
    }
    if color.lower() in named_colors:
        return color.lower()
    
    return None

def validate_typography(typography_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate typography settings"""
    
    validated = {}
    
    # Font family
    if 'font_family' in typography_data:
        font = sanitize_string(typography_data['font_family'])
        if font:
            validated['font_family'] = font
    
    # Font size
    if 'font_size' in typography_data:
        try:
            size = float(typography_data['font_size'])
            if 8 <= size <= 72:  # Reasonable font size range
                validated['font_size'] = size
        except (ValueError, TypeError):
            pass
    
    # Font weight
    if 'font_weight' in typography_data:
        weight = typography_data['font_weight']
        if weight in ['normal', 'bold', 'lighter', 'bolder'] or (isinstance(weight, int) and 100 <= weight <= 900):
            validated['font_weight'] = weight
    
    return validated

def validate_conversion_goals(goals_data: List[str]) -> List[str]:
    """Validate conversion goals list"""
    
    if not isinstance(goals_data, list):
        return []
    
    valid_goals = []
    allowed_goals = [
        'lead_generation', 'sales', 'signups', 'downloads', 'subscriptions',
        'consultations', 'demos', 'trials', 'webinar_registrations', 'phone_calls'
    ]
    
    for goal in goals_data[:5]:  # Max 5 goals
        sanitized_goal = sanitize_string(goal)
        if sanitized_goal in allowed_goals:
            valid_goals.append(sanitized_goal)
    
    return valid_goals

def validate_competitors_data(competitors_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Validate competitor analysis data"""
    
    if not isinstance(competitors_data, list):
        return []
    
    validated_competitors = []
    
    for competitor in competitors_data[:10]:  # Max 10 competitors
        if not isinstance(competitor, dict):
            continue
        
        validated_competitor = {}
        
        # Company name (required)
        if 'name' in competitor:
            name = sanitize_string(competitor['name'])
            if name:
                validated_competitor['name'] = name
            else:
                continue  # Skip if no valid name
        else:
            continue
        
        # URL
        if 'url' in competitor:
            url = validate_url(competitor['url'])
            if url:
                validated_competitor['url'] = url
        
        # Strength score
        if 'strength_score' in competitor:
            score = validate_confidence_score(competitor['strength_score'])
            validated_competitor['strength_score'] = score
        
        # Key features
        if 'key_features' in competitor and isinstance(competitor['key_features'], list):
            validated_competitor['key_features'] = [
                sanitize_string(feature) 
                for feature in competitor['key_features'][:10]
                if sanitize_string(feature)
            ]
        
        # Pricing info
        if 'pricing' in competitor:
            pricing = validate_pricing_info(competitor['pricing'])
            validated_competitor['pricing'] = pricing
        
        validated_competitors.append(validated_competitor)
    
    return validated_competitors

def validate_product_info(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate product information"""
    
    validated = {}
    
    # Product name (required)
    if 'name' in product_data:
        name = sanitize_string(product_data['name'])
        if name:
            validated['name'] = name
        else:
            raise ValidationError("Product name is required")
    else:
        raise ValidationError("Product name is required")
    
    # Description
    if 'description' in product_data:
        description = sanitize_text(product_data['description'])
        if description:
            validated['description'] = description[:1000]  # Max 1000 chars
    
    # Category
    if 'category' in product_data:
        category = sanitize_string(product_data['category'])
        if category:
            validated['category'] = category
    
    # Price
    if 'price' in product_data:
        price = validate_positive_number(product_data['price'], 'price')
        validated['price'] = price
    
    # Benefits
    if 'benefits' in product_data and isinstance(product_data['benefits'], list):
        validated['benefits'] = [
            sanitize_string(benefit) 
            for benefit in product_data['benefits'][:10]
            if sanitize_string(benefit)
        ]
    
    # Features
    if 'features' in product_data and isinstance(product_data['features'], list):
        validated['features'] = [
            sanitize_string(feature) 
            for feature in product_data['features'][:15]
            if sanitize_string(feature)
        ]
    
    return validated

def validate_market_intelligence(market_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate market intelligence data"""
    
    validated = {}
    
    # Market size
    if 'market_size' in market_data:
        size = validate_positive_number(market_data['market_size'], 'market_size')
        validated['market_size'] = size
    
    # Growth rate
    if 'growth_rate' in market_data:
        try:
            growth = float(market_data['growth_rate'])
            validated['growth_rate'] = max(-50, min(200, growth))  # -50% to 200%
        except (ValueError, TypeError):
            pass
    
    # Key trends
    if 'trends' in market_data and isinstance(market_data['trends'], list):
        validated['trends'] = [
            sanitize_string(trend) 
            for trend in market_data['trends'][:10]
            if sanitize_string(trend)
        ]
    
    # Target demographics
    if 'demographics' in market_data:
        validated['demographics'] = validate_target_audience(market_data['demographics'])
    
    return validated

def validate_conversion_intelligence(conv_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate conversion intelligence data"""
    
    validated = {}
    
    # Scientific backing
    if 'scientific_backing' in conv_data:
        sci_backing = conv_data['scientific_backing']
        if isinstance(sci_backing, dict):
            validated_sci = {}
            if 'score' in sci_backing:
                validated_sci['score'] = validate_confidence_score(sci_backing['score'])
            if 'sources' in sci_backing and isinstance(sci_backing['sources'], list):
                validated_sci['sources'] = [
                    validate_url(source) for source in sci_backing['sources'][:5]
                    if validate_url(source)
                ]
            validated['scientific_backing'] = validated_sci
    
    # Emotional triggers
    if 'emotional_triggers' in conv_data:
        triggers = conv_data['emotional_triggers']
        if isinstance(triggers, dict):
            validated_triggers = {}
            if 'effectiveness' in triggers:
                validated_triggers['effectiveness'] = validate_confidence_score(triggers['effectiveness'])
            if 'triggers' in triggers and isinstance(triggers['triggers'], list):
                validated_triggers['triggers'] = [
                    sanitize_string(trigger) 
                    for trigger in triggers['triggers'][:10]
                    if sanitize_string(trigger)
                ]
            validated['emotional_triggers'] = validated_triggers
    
    # Authority indicators
    if 'authority_indicators' in conv_data:
        authority = conv_data['authority_indicators']
        if isinstance(authority, dict):
            validated_auth = {}
            if 'score' in authority:
                validated_auth['score'] = validate_confidence_score(authority['score'])
            if 'indicators' in authority and isinstance(authority['indicators'], list):
                validated_auth['indicators'] = [
                    sanitize_string(indicator) 
                    for indicator in authority['indicators'][:10]
                    if sanitize_string(indicator)
                ]
            validated['authority_indicators'] = validated_auth
    
    return validated

def validate_pricing_info(pricing_data: Any) -> Dict[str, Any]:
    """Validate pricing information"""
    
    validated = {}
    
    if isinstance(pricing_data, dict):
        # Price value
        if 'price' in pricing_data:
            price = validate_positive_number(pricing_data['price'], 'price')
            validated['price'] = price
        
        # Currency
        if 'currency' in pricing_data:
            currency = sanitize_string(pricing_data['currency'])
            if currency and len(currency) <= 5:
                validated['currency'] = currency.upper()
        
        # Billing period
        if 'billing_period' in pricing_data:
            period = sanitize_string(pricing_data['billing_period'])
            if period in ['monthly', 'yearly', 'one-time', 'weekly']:
                validated['billing_period'] = period
    
    elif isinstance(pricing_data, (int, float)):
        # Simple numeric price
        validated['price'] = validate_positive_number(pricing_data, 'price')
    
    return validated

def validate_analytics_event_data(event_data: Dict[str, Any]) -> ValidationResult:
    """Validate analytics event data"""
    
    result = ValidationResult(True, {})
    
    # Required fields
    required_fields = ['content_id', 'event_type']
    for field in required_fields:
        if field not in event_data:
            result.add_error(f"Missing required field: {field}")
        else:
            result.data[field] = event_data[field]
    
    # Validate event type
    if 'event_type' in event_data:
        try:
            event_type = EventType(event_data['event_type'])
            result.data['event_type'] = event_type
        except ValueError:
            result.add_error(f"Invalid event type: {event_data['event_type']}")
    
    # Validate content ID
    if 'content_id' in event_data:
        content_id = sanitize_string(event_data['content_id'])
        if not content_id:
            result.add_error("Invalid content_id")
        else:
            result.data['content_id'] = content_id
    
    # Validate session info
    if 'session_info' in event_data:
        session_info = validate_session_info(event_data['session_info'])
        result.data['session_info'] = session_info
    
    # Validate event-specific data
    if 'event_data' in event_data:
        if isinstance(event_data['event_data'], dict):
            result.data['event_data'] = sanitize_dict(event_data['event_data'])
        else:
            result.add_warning("Event data should be a dictionary")
    
    return result

def validate_session_info(session_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate session information"""
    
    validated = {}
    
    # Session ID
    if 'session_id' in session_data:
        session_id = sanitize_string(session_data['session_id'])
        if session_id:
            validated['session_id'] = session_id
    
    # User fingerprint
    if 'user_fingerprint' in session_data:
        fingerprint = sanitize_string(session_data['user_fingerprint'])
        if fingerprint:
            validated['user_fingerprint'] = fingerprint
    
    # User agent
    if 'user_agent' in session_data:
        user_agent = sanitize_string(session_data['user_agent'])
        if user_agent:
            validated['user_agent'] = user_agent[:500]  # Limit length
    
    # IP address
    if 'ip_address' in session_data:
        ip = validate_ip_address(session_data['ip_address'])
        if ip:
            validated['ip_address'] = ip
    
    # Referrer
    if 'referrer' in session_data:
        referrer = validate_url(session_data['referrer'])
        if referrer:
            validated['referrer'] = referrer
    
    # Device info
    if 'device_info' in session_data:
        device_info = validate_device_info(session_data['device_info'])
        validated['device_info'] = device_info
    
    return validated

def validate_device_info(device_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate device information"""
    
    validated = {}
    
    # Device type
    if 'device_type' in device_data:
        try:
            device_type = DeviceType(device_data['device_type'])
            validated['device_type'] = device_type.value
        except ValueError:
            validated['device_type'] = DeviceType.UNKNOWN.value
    
    # Screen resolution
    if 'screen_resolution' in device_data:
        resolution = sanitize_string(device_data['screen_resolution'])
        if resolution and re.match(r'^\d+x\d+$', resolution):
            validated['screen_resolution'] = resolution
    
    # Viewport size
    if 'viewport_size' in device_data:
        viewport = sanitize_string(device_data['viewport_size'])
        if viewport and re.match(r'^\d+x\d+$', viewport):
            validated['viewport_size'] = viewport
    
    return validated

# Utility validation functions

def validate_confidence_score(score: Any) -> float:
    """Validate confidence score (0.0 to 1.0)"""
    
    try:
        score_float = float(score)
        return max(0.0, min(1.0, score_float))
    except (ValueError, TypeError):
        return 0.5  # Default medium confidence

def validate_positive_integer(value: Any, field_name: str) -> int:
    """Validate positive integer value"""
    
    try:
        int_value = int(value)
        if int_value < 0:
            raise ValidationError(f"{field_name} must be positive")
        return int_value
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a valid integer")

def validate_positive_number(value: Any, field_name: str) -> float:
    """Validate positive number value"""
    
    try:
        float_value = float(value)
        if float_value < 0:
            raise ValidationError(f"{field_name} must be positive")
        return float_value
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a valid number")

def validate_url(url: str) -> Optional[str]:
    """Validate URL format"""
    
    if not isinstance(url, str):
        return None
    
    url = url.strip()
    if not url:
        return None
    
    try:
        result = urlparse(url)
        if all([result.scheme, result.netloc]):
            # Basic security check - only allow http/https
            if result.scheme.lower() in ['http', 'https']:
                return url
    except Exception:
        pass
    
    return None

def validate_ip_address(ip: str) -> Optional[str]:
    """Validate IP address format"""
    
    if not isinstance(ip, str):
        return None
    
    ip = ip.strip()
    
    # IPv4 validation
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ipv4_pattern, ip):
        parts = ip.split('.')
        if all(0 <= int(part) <= 255 for part in parts):
            return ip
    
    # IPv6 basic validation (simplified)
    if ':' in ip and len(ip) <= 39:
        return ip
    
    return None

def sanitize_string(value: Any, max_length: int = 255) -> str:
    """Sanitize string input"""
    
    if not isinstance(value, str):
        value = str(value) if value is not None else ""
    
    # Remove dangerous characters and limit length
    sanitized = bleach.clean(value, tags=[], strip=True)
    sanitized = re.sub(r'[<>"\'\\\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    return sanitized.strip()[:max_length]

def sanitize_text(value: Any, max_length: int = 5000) -> str:
    """Sanitize text input (allows more characters than string)"""
    
    if not isinstance(value, str):
        value = str(value) if value is not None else ""
    
    # Allow basic formatting but remove dangerous content
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'li', 'ul', 'ol']
    sanitized = bleach.clean(value, tags=allowed_tags, strip=True)
    
    return sanitized.strip()[:max_length]

def sanitize_dict(data: Dict[str, Any], max_depth: int = 3) -> Dict[str, Any]:
    """Recursively sanitize dictionary data"""
    
    if max_depth <= 0:
        return {}
    
    sanitized = {}
    
    for key, value in data.items():
        # Sanitize key
        clean_key = sanitize_string(key, 100)
        if not clean_key:
            continue
        
        # Sanitize value based on type
        if isinstance(value, str):
            sanitized[clean_key] = sanitize_string(value, 1000)
        elif isinstance(value, (int, float, bool)):
            sanitized[clean_key] = value
        elif isinstance(value, dict):
            sanitized[clean_key] = sanitize_dict(value, max_depth - 1)
        elif isinstance(value, list):
            sanitized[clean_key] = [
                sanitize_string(item) if isinstance(item, str) else item
                for item in value[:20]  # Limit list size
                if item is not None
            ]
        # Skip other types
    
    return sanitized

def validate_file_upload(file_data: Dict[str, Any]) -> ValidationResult:
    """Validate file upload data"""
    
    result = ValidationResult(True, {})
    
    # File size check
    if 'size' in file_data:
        size = file_data['size']
        max_size = 10 * 1024 * 1024  # 10MB
        if size > max_size:
            result.add_error(f"File size {size} exceeds maximum {max_size} bytes")
    
    # File type check
    if 'type' in file_data:
        file_type = file_data['type'].lower()
        allowed_types = [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'text/plain', 'text/csv', 'application/json',
            'application/pdf'
        ]
        if file_type not in allowed_types:
            result.add_error(f"File type {file_type} not allowed")
    
    # Filename check
    if 'filename' in file_data:
        filename = sanitize_string(file_data['filename'])
        if not filename:
            result.add_error("Invalid filename")
        elif len(filename) > 255:
            result.add_error("Filename too long")
        else:
            result.data['filename'] = filename
    
    return result

# Export validation functions
__all__ = [
    'ValidationError',
    'ValidationResult',
    'validate_preferences',
    'validate_intelligence_data',
    'validate_target_audience',
    'validate_brand_guidelines',
    'validate_analytics_event_data',
    'validate_session_info',
    'validate_confidence_score',
    'validate_positive_integer',
    'validate_positive_number',
    'validate_url',
    'validate_ip_address',
    'sanitize_string',
    'sanitize_text',
    'sanitize_dict',
    'validate_file_upload'
]