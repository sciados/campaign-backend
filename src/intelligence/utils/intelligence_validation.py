"""
File: src/intelligence/utils/intelligence_validation.py
Intelligence Validation Utilities
Helper functions for validating and structuring intelligence data
"""
from typing import Dict, Any


def ensure_intelligence_structure(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure all required intelligence categories exist and are properly structured"""
    
    # Default structure for each intelligence category
    default_offer_intelligence = {
        "products": [],
        "pricing": [],
        "bonuses": [],
        "guarantees": [],
        "value_propositions": [],
        "insights": []
    }
    
    default_psychology_intelligence = {
        "emotional_triggers": [],
        "pain_points": [],
        "target_audience": "General audience",
        "persuasion_techniques": []
    }
    
    default_content_intelligence = {
        "key_messages": [],
        "success_stories": [],
        "social_proof": [],
        "content_structure": "Standard sales page"
    }
    
    default_competitive_intelligence = {
        "opportunities": [],
        "gaps": [],
        "positioning": "Standard approach",
        "advantages": [],
        "weaknesses": []
    }
    
    default_brand_intelligence = {
        "tone_voice": "Professional",
        "messaging_style": "Direct",
        "brand_positioning": "Market competitor"
    }
    
    # Ensure each category exists and merge with defaults
    enhanced_result = analysis_result.copy()
    
    # Merge offer intelligence
    offer_intel = analysis_result.get("offer_intelligence", {})
    if isinstance(offer_intel, dict):
        enhanced_result["offer_intelligence"] = {**default_offer_intelligence, **offer_intel}
    else:
        enhanced_result["offer_intelligence"] = default_offer_intelligence
    
    # Merge psychology intelligence
    psych_intel = analysis_result.get("psychology_intelligence", {})
    if isinstance(psych_intel, dict):
        enhanced_result["psychology_intelligence"] = {**default_psychology_intelligence, **psych_intel}
    else:
        enhanced_result["psychology_intelligence"] = default_psychology_intelligence
    
    # Merge content intelligence
    content_intel = analysis_result.get("content_intelligence", {})
    if isinstance(content_intel, dict):
        enhanced_result["content_intelligence"] = {**default_content_intelligence, **content_intel}
    else:
        enhanced_result["content_intelligence"] = default_content_intelligence
    
    # Merge competitive intelligence
    comp_intel = analysis_result.get("competitive_intelligence", {})
    if isinstance(comp_intel, dict):
        enhanced_result["competitive_intelligence"] = {**default_competitive_intelligence, **comp_intel}
    else:
        enhanced_result["competitive_intelligence"] = default_competitive_intelligence
    
    # Merge brand intelligence
    brand_intel = analysis_result.get("brand_intelligence", {})
    if isinstance(brand_intel, dict):
        enhanced_result["brand_intelligence"] = {**default_brand_intelligence, **brand_intel}
    else:
        enhanced_result["brand_intelligence"] = default_brand_intelligence
    
    return enhanced_result


def validate_intelligence_section(intelligence_data: Any) -> Dict[str, Any]:
    """Validate and clean intelligence section data for database storage"""
    
    if not isinstance(intelligence_data, dict):
        return {}
    
    cleaned_data = {}
    
    for key, value in intelligence_data.items():
        # Ensure key is a string
        if not isinstance(key, str):
            continue
            
        # Clean and validate the value
        if isinstance(value, (list, dict, str, int, float, bool)):
            # Valid JSON serializable types
            if isinstance(value, str) and len(value) > 10000:
                # Truncate overly long strings
                cleaned_data[key] = value[:10000] + "..."
            else:
                cleaned_data[key] = value
        elif value is None:
            cleaned_data[key] = None
        else:
            # Convert other types to string
            cleaned_data[key] = str(value)
    
    return cleaned_data


def validate_content_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Validate content metadata for database storage"""
    if not isinstance(metadata, dict):
        return {}
    
    validated_metadata = {}
    
    # Define allowed metadata fields and their types
    allowed_fields = {
        'word_count': int,
        'estimated_read_time': int,
        'tone': str,
        'style': str,
        'target_audience': str,
        'content_quality_score': float,
        'engagement_predictions': dict,
        'seo_keywords': list,
        'call_to_actions': list,
        'emotional_triggers_used': list
    }
    
    for key, value in metadata.items():
        if key in allowed_fields:
            expected_type = allowed_fields[key]
            try:
                if expected_type == int:
                    validated_metadata[key] = int(value) if value is not None else 0
                elif expected_type == float:
                    validated_metadata[key] = float(value) if value is not None else 0.0
                elif expected_type == str:
                    validated_metadata[key] = str(value) if value is not None else ""
                elif expected_type == list:
                    validated_metadata[key] = list(value) if isinstance(value, (list, tuple)) else []
                elif expected_type == dict:
                    validated_metadata[key] = dict(value) if isinstance(value, dict) else {}
            except (ValueError, TypeError):
                # If conversion fails, use default value
                if expected_type == int:
                    validated_metadata[key] = 0
                elif expected_type == float:
                    validated_metadata[key] = 0.0
                elif expected_type == str:
                    validated_metadata[key] = ""
                elif expected_type == list:
                    validated_metadata[key] = []
                elif expected_type == dict:
                    validated_metadata[key] = {}
    
    return validated_metadata


def sanitize_user_input(input_data: Any, max_length: int = 1000) -> str:
    """Sanitize user input for safe storage"""
    if input_data is None:
        return ""
    
    # Convert to string
    str_data = str(input_data)
    
    # Truncate if too long
    if len(str_data) > max_length:
        str_data = str_data[:max_length] + "..."
    
    # Remove any potentially harmful characters
    # (This is a basic example - you might want more sophisticated sanitization)
    sanitized = str_data.replace('\x00', '').replace('\r\n', '\n').replace('\r', '\n')
    
    return sanitized


def validate_generation_preferences(preferences: Dict[str, Any]) -> Dict[str, Any]:
    """Validate content generation preferences"""
    if not isinstance(preferences, dict):
        return {}
    
    validated_prefs = {}
    
    # Define allowed preference fields and their validation
    allowed_prefs = {
        'tone': ['professional', 'casual', 'friendly', 'authoritative', 'conversational'],
        'style': ['direct', 'storytelling', 'educational', 'persuasive', 'informative'],
        'length': ['short', 'medium', 'long'],
        'target_audience': str,
        'include_statistics': bool,
        'include_testimonials': bool,
        'include_urgency': bool,
        'focus_benefits': bool,
        'focus_features': bool,
        'call_to_action_style': ['soft', 'medium', 'strong'],
        'personalization_level': ['low', 'medium', 'high'],
        'industry_focus': str,
        'brand_voice': str
    }
    
    for key, value in preferences.items():
        if key in allowed_prefs:
            expected = allowed_prefs[key]
            
            if isinstance(expected, list):
                # Validate against allowed values
                if value in expected:
                    validated_prefs[key] = value
                else:
                    # Use first value as default
                    validated_prefs[key] = expected[0]
            
            elif expected == str:
                validated_prefs[key] = sanitize_user_input(value, 200)
            
            elif expected == bool:
                validated_prefs[key] = bool(value) if value is not None else False
            
            elif expected == int:
                try:
                    validated_prefs[key] = int(value)
                except (ValueError, TypeError):
                    validated_prefs[key] = 0
            
            elif expected == float:
                try:
                    validated_prefs[key] = float(value)
                except (ValueError, TypeError):
                    validated_prefs[key] = 0.0
    
    return validated_prefs


def merge_intelligence_data(primary: Dict[str, Any], secondary: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two intelligence data dictionaries, prioritizing primary"""
    if not isinstance(primary, dict):
        return secondary if isinstance(secondary, dict) else {}
    
    if not isinstance(secondary, dict):
        return primary
    
    merged = primary.copy()
    
    for key, value in secondary.items():
        if key not in merged:
            merged[key] = value
        elif isinstance(merged[key], list) and isinstance(value, list):
            # Merge lists, avoiding duplicates
            merged[key] = list(set(merged[key] + value))
        elif isinstance(merged[key], dict) and isinstance(value, dict):
            # Recursively merge dictionaries
            merged[key] = merge_intelligence_data(merged[key], value)
        # For other types, keep the primary value
    
    return merged